## API Key Configuration

### Obtaining Groq API Keys

1. **Create a Groq Account**
   - Visit [Groq's Console](https://console.groq.com)
   - Sign up for a new account or log in

2. **Generate API Keys**
   - Navigate to the API section in your Groq dashboard
   - Generate two separate API keys:
     * First key: Used for initial query generation
     * Second key: Used for final processing
   - Save both keys securely

3. **Configure Environment Variables**
   
   Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

   Add your Groq API keys to the `.env` file:
   ```
   GROQ_API_KEY_1=your_first_groq_api_key
   GROQ_API_KEY_2=your_second_groq_api_key
   ```

   > ⚠️ **Security Note**: 
   > - Keep your API keys confidential
   > - Never commit the `.env` file to version control
   > - Don't share your keys in public repositories
   > - Rotate keys periodically for better security

4. **Verify API Key Setup**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   # Test if keys are properly loaded
   if os.getenv('GROQ_API_KEY_1') and os.getenv('GROQ_API_KEY_2'):
       print("API keys loaded successfully!")
   else:
       print("Error: API keys not found!")
   ```

### Why Two API Keys?

The application uses two separate Groq API keys for:
1. Load balancing between different operations
2. Preventing rate limit issues
3. Separating concerns between initial query generation and final processing
4. Providing redundancy in case one key reaches its rate limit 