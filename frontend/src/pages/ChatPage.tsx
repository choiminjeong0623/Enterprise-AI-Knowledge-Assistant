import { useState } from "react";

import {
    Box,
    Button,
    Container,
    Paper,
    TextField,
    Typography,
} from "@mui/material";

import ChatMessage from "../components/ChatMessage";
import type { ChatMessage as Message } from "../types/chat";
import { chat } from "../api/chat";

export default function ChatPage() {

    const [messages, setMessages] = useState<Message[]>([]);

    const [question, setQuestion] = useState("");

    async function sendMessage() {

        if (!question.trim()) {
            return;
        }

        const userMessage: Message = {
            role: "user",
            content: question,
        };

        setMessages((prev) => [...prev, userMessage]);

        try {

            const response = await chat({
                message: question
            });

            const assistantMessage: Message = {
                role: "assistant",
                content: response.data.answer,
            };

            setMessages((prev) => [
                ...prev,
                assistantMessage,
            ]);

            setQuestion("");

        } catch (error) {

            console.error(error);

            alert("채팅 요청에 실패했습니다.");

        }
    }

    return (

        <Container maxWidth="md">

            <Typography
                variant="h4"
                sx={{ mt: 3, mb: 3 }}
            >
                Enterprise AI Knowledge Assistant
            </Typography>

            <Paper
                sx={{
                    height: "60vh",
                    p: 2,
                    overflowY: "auto",
                    mb: 2,
                }}
            >

                {messages.map((message, index) => (

                    <ChatMessage
                        key={index}
                        message={message}
                    />

                ))}

            </Paper>

            <Box
                sx={{
                    display : "flex",
                    gap : 2
                }}   
            >

                <TextField
                    fullWidth
                    placeholder="질문을 입력하세요."
                    value={question}
                    onChange={(e) =>
                        setQuestion(e.target.value)
                    }
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            sendMessage();
                        }
                    }}
                />

                <Button
                    variant="contained"
                    onClick={sendMessage}
                >
                    Send
                </Button>

            </Box>

        </Container>

    );

}