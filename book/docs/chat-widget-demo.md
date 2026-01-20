---
title: Chat Widget Demo
sidebar_label: Chat Widget
---

# Chat Widget Demo

This page demonstrates the functionality of the chat widget that allows you to ask questions about the book content and receive answers with proper citations.

import BookChatWidget from '@site/src/components/BookChatWidget';

<BookChatWidget />

## How It Works

The chat widget connects to our RAG (Retrieval-Augmented Generation) backend to provide contextual answers based on the book content. When you ask a question:

1. Your question is converted to an embedding vector
2. The vector is compared against document embeddings in our vector database
3. Most relevant document chunks are retrieved
4. The LLM generates a response based on the retrieved context
5. Citations to source documents are provided with the answer

## Features

- **Context-Aware**: The widget can consider selected text as context when answering questions
- **Citations**: All answers include references to the source documents
- **Conversational**: Maintains context across multiple exchanges
- **Responsive**: Works on both desktop and mobile devices

Try asking questions about the book content in the widget above!