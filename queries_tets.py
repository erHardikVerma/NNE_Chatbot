@app.route('/chatbot_query', methods=['POST'])
@login_required
def chatbot_query():
    """Handle chatbot queries with natural language understanding"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'response': 'Please enter a question or search term.'})

        import re
        query_lower = query.lower()

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Detect intent and handle accordingly
        response = ""

        # Intent 0: Conversational/Social Interactions (handle first to avoid treating as search)

        # Greetings
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']):
            response = "Hello! 👋 I'm here to help you track your bikes and orders. You can ask me:\n\n"
            response += "• Search: 'find bbshell N24429207' or 'track frame Y24K30562'\n"
            response += "• Status: 'how many bikes delivered?' or 'show inventory'\n"
            response += "• Timeline: 'when did this cycle dispatch?' or 'when will DRIVE/27 complete?'\n\n"
            response += "What would you like to know?"

        # Thanks/Acknowledgments
        elif any(phrase in query_lower for phrase in ['thank you', 'thanks', 'thank u', 'thnks', 'thnx']) or \
             (any(word in query_lower for word in ['ok', 'okay', 'got it', 'understood', 'cool', 'great', 'nice', 'perfect', 'good']) and len(query.split()) <= 3):
            responses = [
                "You're welcome! Let me know if you need anything else. 😊",
                "Happy to help! Feel free to ask if you have more questions.",
                "Glad I could help! Anything else you'd like to know?",
                "No problem! I'm here if you need me.",
                "Anytime! Just ask if you need to track anything."
            ]
            import random
            response = random.choice(responses)

        # Help requests
        elif any(phrase in query_lower for phrase in ['help', 'what can you do', 'how to use', 'how do i', 'what are you', 'who are you', 'commands', 'options']):
            response = "I can help you with:\n\n"
            response += "🔍 **Search & Track**\n"
            response += "   • Find bikes by BBShell/Frame: 'search N24429207'\n"
            response += "   • Track by Fork: 'find fork F12345'\n"
            response += "   • Search by Serial/PO/Controller/Battery/Motor\n\n"
            response += "📊 **Status & Count**\n"
            response += "   • 'how many bikes delivered?'\n"
            response += "   • 'show inventory'\n"
            response += "   • 'bikes in production'\n\n"
            response += "📅 **Timeline & Dates**\n"
            response += "   • 'when did N24429207 dispatch?'\n"
            response += "   • 'when will DRIVE/27 complete?'\n\n"
            response += "💬 **Tips**:\n"
            response += "   • I understand natural language - just ask!\n"
            response += "   • 'Frame number' and 'BBShell' mean the same thing\n"
            response += "   • You can search using any bike component number"

        # Farewells
        elif any(word in query_lower for word in ['bye', 'goodbye', 'see you', 'see ya', 'later', 'exit', 'quit']) and len(query.split()) <= 3:
            response = "Goodbye! Come back anytime you need to track your bikes. 👋"

        # Small talk / How are you
        elif any(phrase in query_lower for phrase in ['how are you', "how's it going", 'whats up', "what's up", 'how r u', 'how do you do']):
            response = "I'm doing great, thanks for asking! 😊 I'm ready to help you track your bikes and orders. What would you like to know?"

        # About the bot
        elif any(phrase in query_lower for phrase in ['who are you', 'what are you', 'are you a bot', 'are you real', 'are you human']):
            response = "I'm your bike tracking assistant! 🤖 I can help you find bikes, check delivery status, and track orders. I'm powered by AI to understand your questions naturally. What can I help you track today?"

        # Affirmations/Confirmations (yes, sure, etc.)
        elif any(word in query_lower for word in ['yes', 'yeah', 'yep', 'sure', 'alright', 'fine', 'yup']) and len(query.split()) <= 2:
            response = "Great! What would you like me to help you with? You can search for bikes, check status, or ask about delivery dates."

        # Negative responses
        elif any(word in query_lower for word in ['no', 'nope', 'nah', 'not really']) and len(query.split()) <= 3:
            response = "No problem! Let me know if you need anything. I'm here to help you track bikes and orders."

        # Appreciation (beyond thanks)
        elif any(word in query_lower for word in ['awesome', 'amazing', 'excellent', 'brilliant', 'wonderful', 'fantastic']) and len(query.split()) <= 3:
            response = "I'm glad I could help! 🌟 Feel free to ask me anything else about your bikes or orders."

        # Apologies
        elif any(word in query_lower for word in ['sorry', 'apologize', 'my bad', 'my mistake', 'oops']) and len(query.split()) <= 4:
            response = "No worries at all! 😊 How can I help you?"

        # Wait/Hold on
        elif any(phrase in query_lower for phrase in ['wait', 'hold on', 'one sec', 'one second', 'give me a sec', 'just a moment']):
            response = "Take your time! I'll be here when you're ready. ⏰"

        # Praise/Compliments
        elif any(phrase in query_lower for phrase in ['good job', 'well done', 'you are good', 'you are great', 'helpful', 'you rock', 'you are awesome']):
            response = "Thank you so much! 🙏 I'm here to make bike tracking easy for you. What else can I help with?"

        # Asking for recommendations
        elif any(phrase in query_lower for phrase in ['what should i', 'what can i', 'suggest', 'recommend', 'what to do']):
            response = "I can help you:\n• Track a specific bike by searching its BBShell/Frame number\n• Check how many bikes are delivered or in production\n• See when a PO will be completed\n• Find bikes by any component number\n\nWhat would you like to check?"

        # Confusion/Unclear
        elif any(phrase in query_lower for phrase in ['what', 'huh', 'unclear', "don't understand", 'confused']) and len(query.split()) <= 5:
            response = "I'm here to help you track bikes and orders! Try asking:\n"
            response += "• 'search bbshell N24429207'\n"
            response += "• 'how many bikes delivered?'\n"
            response += "• 'when did this cycle dispatch?'\n\n"
            response += "Or type 'help' to see all options."

        # Intent 1: Inventory-specific questions (check first before general status)
        elif 'inventory' in query_lower or 'stock' in query_lower or 'invento' in query_lower:
            # Count bikes in inventory
            cursor.execute("""
                SELECT COUNT(*) as count FROM bike
                INNER JOIN client ON bike.client = client.id
                WHERE client.user = %s AND bike.station = 'Inventory'
            """, (current_user.id,))
            result = cursor.fetchone()
            response = f"📦 You have {result['count']} bikes currently in inventory.\n\n"
            response += "💡 Tip: Ask 'show inventory' to see the latest bikes in stock."

        # Intent 2: Status/Count Questions
        elif any(word in query_lower for word in ['status', 'how many', 'count', 'total', 'number of']):
            if 'delivered' in query_lower or 'dispatch' in query_lower:
                # Count delivered bikes
                cursor.execute("""
                    SELECT COUNT(*) as count FROM bike
                    INNER JOIN client ON bike.client = client.id
                    WHERE client.user = %s AND bike.dispatchtime IS NOT NULL
                """, (current_user.id,))
                result = cursor.fetchone()
                response = f"✅ You have {result['count']} bikes that have been delivered/dispatched."

            elif 'process' in query_lower or 'production' in query_lower or 'producing' in query_lower or 'manufacture' in query_lower:
                # Count bikes in process
                cursor.execute("""
                    SELECT COUNT(*) as count FROM bike
                    INNER JOIN client ON bike.client = client.id
                    WHERE client.user = %s AND bike.inProcess = 1
                """, (current_user.id,))
                result = cursor.fetchone()
                response = f"⚙️ You have {result['count']} bikes currently in production."

            elif 'order' in query_lower or 'po' in query_lower or 'purchase' in query_lower:
                # Count total orders
                cursor.execute("""
                    SELECT COUNT(DISTINCT po.id) as count FROM po
                    INNER JOIN client ON po.client = client.id
                    WHERE client.user = %s
                """, (current_user.id,))
                result = cursor.fetchone()
                response = f"📋 You have {result['count']} purchase orders in the system."

            elif 'pending' in query_lower or 'waiting' in query_lower or 'remaining' in query_lower:
                # Count pending bikes
                cursor.execute("""
                    SELECT COUNT(*) as count FROM bike
                    INNER JOIN client ON bike.client = client.id
                    WHERE client.user = %s AND bike.dispatchtime IS NULL AND bike.station != 'Inventory'
                """, (current_user.id,))
                result = cursor.fetchone()
                response = f"⏳ You have {result['count']} bikes pending (not yet dispatched or in inventory)."

            else:
                # Total bikes
                cursor.execute("""
                    SELECT COUNT(*) as count FROM bike
                    INNER JOIN client ON bike.client = client.id
                    WHERE client.user = %s
                """, (current_user.id,))
                result = cursor.fetchone()
                response = f"📊 You have a total of {result['count']} bikes in the system."