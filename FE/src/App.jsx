import { createBrowserRouter, createRoutesFromElements, Navigate, Route, RouterProvider } from 'react-router-dom'

import { Navigate } from "react-router-dom";
import useAuth from "../src/hooks/useAuth";
import { AuthProvider } from './context/AuthContext';


function PrivateRoute({ children, roles }) {
  const { user, loading } = useAuth();

  if (loading) return <p>Loading...</p>;
  if (!user) return <Navigate to="/login" />;

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/" />;
  }

  if (requireKyc && user.role !== "consumer" && user.kyc_status !== "approved") {
    return <Navigate to="/kyc" />;
  }

  return children;
}
export default function App() {
    const router=createBrowserRouter(createRoutesFromElements(
    <AuthProvider>
        <Route>
          <Route path="/" element={<ConsumerSite/>} />
          <Route path="/product/:id" element={<ProductPage/>} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/cart"
            element={
              <PrivateRoute roles={["consumer"]}>
                <Cart />
              </PrivateRoute>
            }
          />
          <Route
            path="/checkout"
            element={
              <PrivateRoute roles={["consumer"]}>
                <Checkout />
              </PrivateRoute>
            }
          />

          <Route
            path="/dashboard"
            element={
              <PrivateRoute
                roles={["farmer", "aggregator", "retailer", "admin"]}
                requireKyc={true}
              >
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/kyc"
            element={
              <PrivateRoute
                roles={["farmer", "aggregator", "retailer", "admin"]}
              >
                <KycUpload />
              </PrivateRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<NotFound />} />
        </Route>
    </AuthProvider>
    ))
  return (
    <RouterProvider router={router} />
  );
}