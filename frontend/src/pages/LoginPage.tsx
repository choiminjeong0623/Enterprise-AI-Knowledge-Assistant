import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/auth";
import { setAccessToken } from "../utils/authStorage";
import "./LoginPage.css";

function LoginPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLogin = async () => {
    const trimmedUsername = username.trim();

    if (!trimmedUsername || !password || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const response = await login({
        username: trimmedUsername,
        password,
      });

      setAccessToken(response.access_token);
      navigate("/", { replace: true });
    } catch {
      setErrorMessage("로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-page__card">
        <h1 className="login-page__title">
          Enterprise AI Knowledge Assistant
        </h1>

        <p className="login-page__subtitle">Sign in to continue</p>

        {errorMessage && (
          <div className="login-page__error">{errorMessage}</div>
        )}

        <div className="login-page__form">
          <label className="login-page__label">
            Email
            <input
              className="login-page__input"
              type="email"
              value={username}
              autoComplete="username"
              onChange={(event) => setUsername(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleLogin();
                }
              }}
            />
          </label>

          <label className="login-page__label">
            Password
            <input
              className="login-page__input"
              type="password"
              value={password}
              autoComplete="current-password"
              onChange={(event) => setPassword(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleLogin();
                }
              }}
            />
          </label>

          <button
            type="button"
            className="login-page__button"
            onClick={handleLogin}
            disabled={isSubmitting || !username.trim() || !password}
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;