import client from "./client";

export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export async function login(request: LoginRequest) {

    const params = new URLSearchParams();

    params.append("username", request.username);
    params.append("password", request.password);

    const response = await client.post<LoginResponse>(
        "/auth/login",
        params,
        {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        }
    );

    return response.data;
}