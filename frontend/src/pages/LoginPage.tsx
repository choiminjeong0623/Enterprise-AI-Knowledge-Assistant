import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    Button,
    Container,
    Paper,
    TextField,
    Typography,
} from "@mui/material";

import { login } from "../api/auth";

export default function LoginPage() {

    const navigate = useNavigate();

    const [username, setUsername] = useState("");

    const [password, setPassword] = useState("");

    async function handleLogin() {

        try {

            const response = await login({

                username,

                password

            });

            localStorage.setItem(
                "access_token",
                response.access_token
            );
            console.log("111")
            navigate("/chat");

        } catch (e) {

            console.log(e)

            alert("로그인 실패");

        }

    }

    return (

        <Container maxWidth="sm">

            <Paper sx={{ p: 4, mt: 10 }}>

                <Typography
                    variant="h4"
                    sx={{
                        mb:3
                    }}
                >
                    Enterprise AI
                </Typography>

                <TextField

                    fullWidth

                    label="Username"

                    margin="normal"

                    value={username}

                    onChange={(e)=>

                        setUsername(e.target.value)

                    }

                />

                <TextField

                    fullWidth

                    type="password"

                    label="Password"

                    margin="normal"

                    value={password}

                    onChange={(e)=>

                        setPassword(e.target.value)

                    }

                />

                <Button

                    fullWidth

                    variant="contained"

                    sx={{ mt:2 }}

                    onClick={handleLogin}

                >

                    Login

                </Button>

            </Paper>

        </Container>

    );

}