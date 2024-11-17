A sophisticated, Streamlit-based dashboard that leverages dual LLM processing and advanced search capabilities to extract structured information from web sources. This implementation goes beyond basic requirements with several innovative features and architectural decisions.

## 🌟 Unique Features & Enhancements

### 1. Dual LLM Processing Architecture
- **Load Balanced LLM Processing**: Utilizes two separate Groq API keys for different processing stages:
  - First LLM: Handles initial query generation and optimization
  - Second LLM: Manages final result processing and formatting
- **Benefits**: Improved reliability, better rate limit handling, and parallel processing capabilities

### 2. Advanced Query Processing
- **Multi-Stage Query Pipeline**:
  1. Initial query generation with context awareness
  2. Search execution with DuckDuckGo integration
  3. Result processing with behavioral controls
  4. Final formatting with strict output validation

### 3. Robust Error Handling
- **Rate Limit Management**: Intelligent retry mechanism with exponential backoff
- **Query Validation**: Pre-execution validation to prevent unnecessary API calls
- **Result Verification**: Multi-stage verification of extracted data

### 4. Enhanced Data Processing
- **Column Selection Intelligence**: 
  - Smart column type detection
  - Multi-column correlation support
  - Dynamic query adjustment based on selected columns

### 5. Progress Tracking
- **Detailed Progress Monitoring**:
  - Entity-level progress bars
  - Query-specific status updates
  - Real-time processing statistics

### 6. Structured Output Control
- **Strict Output Formatting**:
  - Consistent JSON/List structure
  - Type validation for extracted data
  - Automated data cleaning and formatting

## 🔧 Technical Improvements

### Architecture
- **Modular Component Design**:
  - Separate services for data processing, LLM interaction, and CSV handling
  - Clean separation of concerns between UI and business logic
  - Extensible plugin architecture for future enhancements

### Performance
- **Optimized Processing**:
  - Batch processing capabilities
  - Caching of intermediate results
  - Efficient memory management for large datasets

### Security
- **Enhanced Security Measures**:
  - API key rotation support
  - Rate limit monitoring
  - Secure credential management

## 🚀 Getting Started

## Project Description
The AI Data Extraction Dashboard is designed to:
- Allow users to upload CSV files or connect to Google Sheets for data input.
- Enable custom query inputs for web searches.
- Integrate with search APIs and LLMs to process search results and extract relevant information.
- Display the extracted data in a structured table and provide download options.

## Key Features
1. **Data Input**:
   - Upload CSV files or connect a Google Sheet.
   - View a preview of the uploaded data.
   - Select the primary column (e.g., company names) for queries.

2. **Custom Query Input**:
   - Define custom prompts like "Get me the email address of company".

3. **Automated Web Search**:
   - Use APIs such as SerpAPI or ScraperAPI and DuckDuckGo search engine API to gather web search results.
   - Store results in a structured format for LLM processing.

4. **LLM Integration**:
   - Process web search results using an LLM.
   - Extract specific information based on user-defined prompts.

5. **Result Display and Export**:
   - Display extracted information in a user-friendly table.
   - Option to download results as a CSV.

## Prerequisites
- **Python 3.8 or higher**
- **Streamlit** for the user interface
- **pandas** for data handling
- **API keys** for:
  - Search API
  - LLM API


## Installation and Setup
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <project-directory>
2.  **Create and Activate a Virtual Environment and Install Dependencies:**:

```bash
python -m venv venv
source venv/bin/activate  
```
#### On Windows: 
```bash
pip install -r requirements.txt

```

3. **Set Up Environment Variables: Create a .env file in the root directory:**

```bash
touch .env
```
Add the following lines to .env:

```
GROQ_API_KEY_1 = your_first_groq_api_key
GROQ_API_KEY_2 = your_second_groq_api_key
```
# **⚠️ Note: Ensure the .env file is added to .gitignore to prevent accidental exposure of API keys.**

4. **Run the Application:**

```
streamlit run dashboard/main.py

## 📊 Usage Examples

### Basic Usage
```python
# Example of using the dashboard for basic data extraction
streamlit run dashboard/main.py
```

### Advanced Query Configuration
```python
# Example of configuring advanced queries
{
    "query_type": "company_info",
    "fields": ["email", "address", "phone"],
    "validation": "strict"
}
```

## 🔍 Implementation Details

### Query Processing Pipeline
1. **Query Generation**:
   - Context-aware query formulation
   - Automatic query optimization
   - Relevance scoring

2. **Search Execution**:
   - Rate-limited search requests
   - Result caching
   - Error recovery

3. **Data Extraction**:
   - Multi-stage validation
   - Format standardization
   - Quality checks

## 🎯 Future Enhancements
### LLM and Training Improvements
- **Enhanced Training Dataset**:
  - Curate specialized datasets for different industries
  - Implement fine-tuning capabilities for domain-specific queries
  - Create validation datasets for accuracy testing

### Database Integration
- **Persistent Storage Solutions**:
  - Integration with PostgreSQL/MongoDB for result storage
  - Caching layer for frequently accessed data
  - Historical query tracking and analytics
  - User preferences and query templates storage

### Advanced LangChain Integration
- **Extended LangChain Capabilities**:
  - Implementation of LangChain Agents for autonomous decision-making
  - Integration with LangChain Memory for context retention
  - Utilization of LangChain Tools for enhanced web scraping
  - Custom LangChain chains for specialized data processing

### Search and Processing
- Integration with additional search APIs (Bing, Google Custom Search)
- Advanced caching mechanisms for faster response times
- Parallel processing for bulk queries

### Validation and Export
- Custom validation rules for industry-specific data
- Export templates for different use cases
- Automated data quality checks

### User Experience
- Interactive query builder interface
- Real-time processing statistics
- Advanced error reporting and suggestions

## 📝 Notes
- This implementation focuses on reliability and scalability
- Designed for both small and large-scale data processing
- Emphasizes data quality and accuracy
