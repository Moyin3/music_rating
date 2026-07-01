import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import {Routes, Route } from "react-router";
import SignUpPage from "./pages/SignUpPage";
function App() {
  return (
    <>
    <Routes>
      <Route path = "/" element = {<HomePage />}></Route>
      <Route path= "/login" element = {<LoginPage />}></Route>
      <Route path = "/sign-up" element = {<SignUpPage />}></Route>
    </Routes>
    </>
  );
}

export default App;
