from pyrogram import Client, filters
import asyncio
import re

# Your API ID, API Hash, and Bot Token
api_id = 28610306
api_hash = '3f57cc57f8883bd604baf3b814ffe023'
user_phone_number = '9521238545'
bot_token = '7421115045:AAEsatiWO20RfqPyKMrVu46_-CK4WyhNntw'

# Create a client instance for the user
user_app = Client("my_account", api_id=api_id, api_hash=api_hash, phone_number=user_phone_number)

# Create a client instance for the bot
bot_app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Recipient username for Quotex Partner Bot
recipient_username = "@QuotexPartnerBot"

# Private group ID for the VIP group (ensure the bot is an admin in this group)
private_group_id = your_group_id  # Replace with your actual group ID

# Function to handle the /start command from the bot
@bot_app.on_message(filters.command("start"))
async def start_handler(client, message):
    user_first_name = message.from_user.first_name
    welcome_message = (
        f"Welcome {user_first_name} to Quotex Auto-Verify Trader ID Bot! "
        "Please enter your trader ID here (only numbers). After successful verification, "
        "we will add you to our VIP group!"
    )
    await client.send_message(message.chat.id, welcome_message)

# Function to handle incoming messages from the bot
@bot_app.on_message(filters.text & ~filters.command("start"))
async def handle_trader_id(client, message):
    trader_id = message.text.strip()
    
    # Check if the message is exactly 8 digits
    if trader_id.isdigit() and len(trader_id) == 8:
        async with user_app:
            # Send the trader ID to @QuotexPartnerBot
            await user_app.send_message(recipient_username, trader_id)
            
            # Wait for a response from @QuotexPartnerBot
            await asyncio.sleep(5)  # Adjust the wait time if necessary
            
            # Check for the verification response
            async for msg in user_app.get_chat_history(recipient_username, limit=1):
                if trader_id in msg.text:
                    if "Trader with ID = '{}' was not found".format(trader_id) in msg.text:
                        await client.send_message(message.chat.id, 
                            "Dear Member,

It appears that your account is not registered using my referral link.

https://broker-qx.pro/sign-up/?lid=569152

Sign Up using above link and deposit 40$ to get entry in VIP group.")
                    else:
                        # Extract Deposits Sum using regular expression
                        deposits_sum_match = re.search(r"Deposits Sum: \$ ([\d\.]+)", msg.text)
                        if deposits_sum_match:
                            deposits_sum = float(deposits_sum_match.group(1))
                            if deposits_sum >= 40:
                                await client.send_message(message.chat.id, "✅ You are verified!")
                                
                                # Generate a one-time invite link for the private group
                                try:
                                    invite_link = await bot_app.create_chat_invite_link(
                                        chat_id=private_group_id,
                                        member_limit=1  # Only one use allowed
                                    )
                                    
                                    await client.send_message(message.chat.id, 
                                        f"Welcome to our VIP group! Here is your one-time invite link: {invite_link.invite_link}")
                                except Exception as e:
                                    await client.send_message(message.chat.id, 
                                        f"An error occurred while creating the invite link: {e}")
                                    print(f"Error: {e}")
                            else:
                                await client.send_message(message.chat.id,
                                    "???? Dear Member,

You are on our Referral link, deposit $40 to your Quotex Account to get entry in our VIP group!

Try again after you have done your deposit!")
                    break
    else:
        await client.send_message(message.chat.id, "Trader ID must consist of 8 numbers.")

# Run both clients
if __name__ == "__main__":
    bot_app.run()