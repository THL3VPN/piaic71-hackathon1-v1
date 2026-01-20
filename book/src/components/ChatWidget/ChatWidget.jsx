import React, { useState, useRef, useEffect } from 'react';
import './ChatWidget.css';

/**
 * ChatWidget Component
 * A reusable chat interface for interacting with the RAG backend API
 */
const ChatWidget = ({ selectedText = null }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Function to send message to backend
  const sendMessage = async (text) => {
    if (!text.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      // Add user message to UI immediately
      const userMessage = {
        id: Date.now(),
        text: text,
        sender: 'user',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, userMessage]);

      // Prepare the request body
      const requestBody = {
        message: text,
        session_id: sessionId || null
      };

      // Include selected text context if available
      if (selectedText) {
        requestBody.context = selectedText;
      }

      // Call the backend API
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Update session ID if new session was created
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // Add assistant response to messages
      const assistantMessage = {
        id: Date.now() + 1,
        text: data.answer,
        sender: 'assistant',
        citations: data.citations || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to get response. Please try again.');

      // Add error message to UI
      const errorMessage = {
        id: Date.now(),
        text: 'Sorry, I\'m having trouble connecting to the service. Please try again.',
        sender: 'assistant',
        isError: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      sendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <h3>Book Assistant</h3>
        {selectedText && (
          <div className="selected-text-context">
            <small>Context: "{selectedText.substring(0, 80)}{selectedText.length > 80 ? '...' : ''}"</small>
          </div>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>Ask a question about the book content, and I'll help you find relevant information with citations.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
            >
              <div className="message-content">
                <p>{message.text}</p>
                {message.citations && message.citations.length > 0 && (
                  <div className="citations">
                    <strong>Citations:</strong>
                    <ul>
                      {message.citations.map((citation, index) => (
                        <li key={index}>
                          {citation.title || citation.source_path || `Source ${index + 1}`}
                          {citation.page_number && ` (Page ${citation.page_number})`}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <div className="timestamp">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the book..."
          disabled={isLoading}
          rows="1"
        />
        <button type="submit" disabled={isLoading || !inputValue.trim()}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
    </div>
  );
};

export default ChatWidget;