import React, { useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

function App() {

  // -----------------------------------------
  // CHAT STATE
  // -----------------------------------------

  const [messages, setMessages] = useState([]);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);


  // -----------------------------------------
  // MODE
  // -----------------------------------------

  const [mode, setMode] = useState("chat");


  // -----------------------------------------
  // CONVERSATION
  // -----------------------------------------

  const [conversationId] = useState(
    () => `conversation-${Date.now()}`
  );


  // -----------------------------------------
  // DOCUMENT STATE
  // -----------------------------------------

  const [selectedFile, setSelectedFile] =
    useState(null);

  const [storeName, setStoreName] =
    useState("");

  const [uploading, setUploading] =
    useState(false);

  const [documentStatus, setDocumentStatus] =
    useState("");


  // -----------------------------------------
  // SEND MESSAGE
  // -----------------------------------------

  const sendMessage = async () => {

    if (!input.trim() || loading) {
      return;
    }


    const currentMessage = input.trim();


    // Add user message immediately

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: currentMessage
      }
    ]);


    setInput("");

    setLoading(true);


    try {

      let response;


      // -------------------------------------
      // NORMAL CHAT
      // -------------------------------------

      if (mode === "chat") {

        response = await axios.post(
          `${API_URL}/chat/`,
          {
            message: currentMessage,
            conversation_id: conversationId
          }
        );

      }


      // -------------------------------------
      // AGENT
      // -------------------------------------

      else if (mode === "agent") {

        response = await axios.post(
          `${API_URL}/agent/`,
          {
            message: currentMessage
          }
        );

      }


      // -------------------------------------
      // DOCUMENT / RAG
      // -------------------------------------

      else if (mode === "document") {

        if (!storeName) {

          throw new Error(
            "Please upload a document first."
          );

        }


        response = await axios.post(
          `${API_URL}/documents/ask`,
          {
            question: currentMessage,
            store_name: storeName
          }
        );

      }


      // -------------------------------------
      // GET RESPONSE
      // -------------------------------------

      let answer;


      if (mode === "document") {

        answer = response.data.answer;

      } else {

        answer = response.data.response;

      }


      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            answer || "No response received."
        }
      ]);


    } catch (error) {

      console.error(
        "Request error:",
        error
      );


      let errorMessage =
        "Something went wrong. Please try again.";


      if (
        error.response &&
        error.response.data
      ) {

        if (
          typeof error.response.data.detail ===
          "string"
        ) {

          errorMessage =
            error.response.data.detail;

        }

      }


      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `❌ ${errorMessage}`
        }
      ]);

    } finally {

      setLoading(false);

    }
  };


  // -----------------------------------------
  // ENTER KEY
  // -----------------------------------------

  const handleKeyDown = (event) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendMessage();

    }
  };


  // -----------------------------------------
  // CREATE DOCUMENT STORE
  // -----------------------------------------

  const createDocumentStore = async () => {

    const response = await axios.post(
      `${API_URL}/documents/store`,
      null,
      {
        params: {
          name: "DSTRAIX Knowledge Base"
        }
      }
    );


    const newStoreName =
      response.data.store_name;


    setStoreName(
      newStoreName
    );


    return newStoreName;
  };


  // -----------------------------------------
  // UPLOAD DOCUMENT
  // -----------------------------------------

  const uploadDocument = async () => {

    if (!selectedFile) {

      setDocumentStatus(
        "Please select a file first."
      );

      return;

    }


    setUploading(true);

    setDocumentStatus(
      "Creating knowledge store..."
    );


    try {

      // -------------------------------------
      // Create a store
      // -------------------------------------

      const newStore =
        await createDocumentStore();


      setDocumentStatus(
        "Uploading and indexing document..."
      );


      // -------------------------------------
      // FormData
      // -------------------------------------

      const formData =
        new FormData();


      formData.append(
        "file",
        selectedFile
      );


      // -------------------------------------
      // Upload
      // -------------------------------------

      await axios.post(
        `${API_URL}/documents/upload`,
        formData,
        {
          params: {
            store_name: newStore
          },
          headers: {
            "Content-Type":
              "multipart/form-data"
          }
        }
      );


      setDocumentStatus(
        `✓ ${selectedFile.name} uploaded successfully`
      );


      // Automatically switch to document mode

      setMode("document");


    } catch (error) {

      console.error(
        "Upload error:",
        error
      );


      let message =
        "Document upload failed.";


      if (
        error.response?.data?.detail
      ) {

        message =
          error.response.data.detail;

      }


      setDocumentStatus(
        `❌ ${message}`
      );

    } finally {

      setUploading(false);

    }
  };


  // -----------------------------------------
  // CLEAR CHAT
  // -----------------------------------------

  const clearChat = () => {

    setMessages([]);

  };


  // -----------------------------------------
  // UI
  // -----------------------------------------

  return (

    <div className="app">


      {/* ================================= */}
      {/* HEADER */}
      {/* ================================= */}

      <header className="header">

        <div className="brand">

          <div className="brand-logo">
            D
          </div>

          <div>

            <h1>
              DSTRAIX
            </h1>

            <span>
              AI Assistant
            </span>

          </div>

        </div>


        {/* MODE SELECTOR */}

        <div className="mode-selector">

          <button
            className={
              mode === "chat"
                ? "mode-button active"
                : "mode-button"
            }
            onClick={() =>
              setMode("chat")
            }
          >
            💬 Chat
          </button>


          <button
            className={
              mode === "agent"
                ? "mode-button active"
                : "mode-button"
            }
            onClick={() =>
              setMode("agent")
            }
          >
            🤖 Agent
          </button>


          <button
            className={
              mode === "document"
                ? "mode-button active"
                : "mode-button"
            }
            onClick={() =>
              setMode("document")
            }
          >
            📚 Document
          </button>

        </div>


        <div className="header-right">

          <span className="online-dot">
            ●
          </span>

          <span>
            Online
          </span>

        </div>

      </header>


      {/* ================================= */}
      {/* MAIN CHAT */}
      {/* ================================= */}

      <main className="chat-container">


        {/* EMPTY STATE */}

        {messages.length === 0 && (

          <div className="welcome">

            <div className="welcome-icon">
              ✦
            </div>

            <h2>
              Welcome to DSTRAIX
            </h2>

            <p>
              Your intelligent AI assistant
              for conversations, documents
              and intelligent tasks.
            </p>


            <div className="feature-cards">

              <div
                className="feature-card"
                onClick={() =>
                  setMode("chat")
                }
              >

                <div>
                  💬
                </div>

                <h3>
                  Chat
                </h3>

                <p>
                  Ask anything and have
                  natural conversations.
                </p>

              </div>


              <div
                className="feature-card"
                onClick={() =>
                  setMode("agent")
                }
              >

                <div>
                  🤖
                </div>

                <h3>
                  Agent
                </h3>

                <p>
                  Let DSTRAIX use tools
                  to solve tasks.
                </p>

              </div>


              <div
                className="feature-card"
                onClick={() =>
                  setMode("document")
                }
              >

                <div>
                  📚
                </div>

                <h3>
                  RAG
                </h3>

                <p>
                  Ask questions about
                  your documents.
                </p>

              </div>

            </div>

          </div>

        )}


        {/* MESSAGES */}

        <div className="messages">

          {messages.map(
            (message, index) => (

              <div
                key={index}
                className={
                  message.role === "user"
                    ? "message user-message"
                    : "message assistant-message"
                }
              >

                <div className="avatar">

                  {message.role === "user"
                    ? "You"
                    : "D"}

                </div>


                <div className="message-body">

                  <div className="message-name">

                    {message.role === "user"
                      ? "You"
                      : "DSTRAIX"}

                  </div>


                  <div className="message-content">

                    {message.content}

                  </div>

                </div>

              </div>

            )
          )}


          {/* LOADING */}

          {loading && (

            <div className="message assistant-message">

              <div className="avatar">
                D
              </div>

              <div className="message-body">

                <div className="message-name">
                  DSTRAIX
                </div>

                <div className="message-content">

                  <div className="typing">

                    <span></span>
                    <span></span>
                    <span></span>

                  </div>

                </div>

              </div>

            </div>

          )}

        </div>

      </main>


      {/* ================================= */}
      {/* DOCUMENT UPLOAD */}
      {/* ================================= */}

      <section className="document-section">

        <div className="document-upload">

          <label
            className="file-label"
          >

            📎

            <span>

              {selectedFile
                ? selectedFile.name
                : "Choose PDF / TXT / MD / DOCX"}

            </span>

            <input
              type="file"
              accept=".pdf,.txt,.md,.docx"
              onChange={(event) => {

                setSelectedFile(
                  event.target.files?.[0] || null
                );

                setDocumentStatus("");

              }}
            />

          </label>


          <button
            className="upload-button"
            onClick={uploadDocument}
            disabled={
              uploading ||
              !selectedFile
            }
          >

            {uploading
              ? "Uploading..."
              : "Upload"}

          </button>


          {documentStatus && (

            <span className="document-status">

              {documentStatus}

            </span>

          )}

        </div>

      </section>


      {/* ================================= */}
      {/* INPUT */}
      {/* ================================= */}

      <section className="input-section">

        <div className="input-box">

          <textarea
            value={input}
            onChange={(event) =>
              setInput(
                event.target.value
              )
            }
            onKeyDown={handleKeyDown}
            placeholder={
              mode === "chat"
                ? "Ask DSTRAIX anything..."
                : mode === "agent"
                ? "Ask the DSTRAIX agent..."
                : "Ask something about your document..."
            }
            rows="1"
          />


          <button
            className="send-button"
            onClick={sendMessage}
            disabled={
              loading ||
              !input.trim()
            }
          >

            ➤

          </button>

        </div>


        <div className="input-footer">

          <span>

            Mode:
            {" "}

            <strong>
              {mode === "chat"
                ? "Chat"
                : mode === "agent"
                ? "Agent"
                : "Document RAG"}
            </strong>

          </span>


          <button
            className="clear-button"
            onClick={clearChat}
          >
            Clear chat
          </button>

        </div>

      </section>

    </div>

  );
}

export default App;