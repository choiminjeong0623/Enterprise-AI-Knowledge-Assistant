import { Navigate } from "react-router-dom";
import { isAuthenticated } from "../../utils/authStorage";

interface PublicOnlyRouteProps {
  children: React.ReactNode;
}

function PublicOnlyRoute({ children }: PublicOnlyRouteProps) {
  if (isAuthenticated()) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

export default PublicOnlyRoute;