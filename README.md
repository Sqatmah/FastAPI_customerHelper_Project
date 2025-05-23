# Customer Support Helper API 🚀

An AI-assisted FastAPI application to enhance customer support interactions. This API helps businesses streamline responses to FAQs, process user-submitted support tickets with sentiment analysis, and recognize user intent for simple actions like tracking orders.

## 🌟 Features

- **FAQ Matching**: Keyword-based response engine for common customer questions.
- **Support Ticket System**: Users can submit support tickets, which are stored with a sentiment score and timestamp.
- **Sentiment Analysis**: Each ticket is analyzed using NLP (TextBlob) to determine the mood of the customer (positive, neutral, negative).
- **Intent Recognition**: Recognizes basic customer intents using regular expressions (e.g., greetings or tracking orders).
- **Clean and Interactive Docs**: Automatically generated documentation with Swagger UI.

---

## 📦 Tech Stack

- **Python 3.10+**
- **FastAPI** — Web framework
- **TextBlob** — Sentiment analysis
- **Pydantic** — Data validation
- **Uvicorn** — ASGI server
- **Regex (re)** — Lightweight intent recognition
- **UUID** — Unique ticket IDs

---

## 🔧 Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/customer-support-api.git
   cd customer-support-api
   ```

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn textblob
   ```

3. **Download TextBlob corpora** (required for sentiment analysis):
   ```bash
   python -m textblob.download_corpora
   ```

4. **Run the API**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Explore the interactive API docs**:
   - Open your browser and go to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📚 API Endpoints Overview

### 🔍 `POST /support/faq`
- **Purpose**: Search for answers in the FAQ database.
- **Input**: User query (string)
- **Output**: Matching question and answer

### 📝 `POST /support/ticket`
- **Purpose**: Submit a support ticket with sentiment analysis.
- **Input**: Email and issue description
- **Output**: Ticket ID, sentiment, and timestamp

### 📬 `GET /support/tickets/{ticket_id}`
- **Purpose**: Check the status and sentiment of a submitted ticket.

### 🧠 `POST /support/action`
- **Purpose**: Recognize basic intents like greeting or tracking orders.

---

## 💡 Example

```bash
curl -X POST "http://127.0.0.1:8000/support/faq" \
-H "Content-Type: application/json" \
-d '{"query": "How do I change my password?"}'
```

---

## 🗃 Sample FAQ Categories

- Password Reset
- Shipping Information
- Return Policy
- Payment Options

> You can extend the `faq_database` dictionary easily by adding new FAQs with associated keywords.

---

## 🚀 Future Improvements

- Replace in-memory databases with persistent storage (e.g., PostgreSQL)
- Add JWT-based user authentication
- Integrate with third-party ticketing systems
- Improve intent recognition using NLP models (e.g., spaCy or transformers)

---

## 🤝 Contributing

Feel free to fork the project, submit PRs, or suggest improvements via issues.

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for more information.

---

## ✨ Author

**Saifeddin Qatmah**  
📧 Email: sqatmah@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/saifeddin-qatamh-a161b2166) | [GitHub](https://github.com/Sqatmah)

---
