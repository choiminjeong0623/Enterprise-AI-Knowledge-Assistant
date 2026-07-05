import { Box, Paper, Typography } from "@mui/material";
import type { ChatMessage as Message } from "../types/chat";

interface Props {
    message: Message;
}

export default function ChatMessage({ message }: Props) {

    const isUser = message.role === "user";

    return (
        <Box
            sx={{
                display:"flex",
                justifyContent: isUser ? "flex-end" : "flex-start",
                mb: 2
            }}
        >
            <Paper
                sx={{
                    p: 2,
                    maxWidth: "70%",
                    backgroundColor: isUser ? "#1976d2" : "#f5f5f5",
                    color: isUser ? "white" : "black",
                }}
            >
                <Typography>
                    {message.content}
                </Typography>
            </Paper>
        </Box>
    );
}