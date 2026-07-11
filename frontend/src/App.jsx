import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import {Routes, Route } from "react-router";
import SignUpPage from "./pages/SignUpPage";
import ContentPage from "./pages/ContentPage";
import ContentRatingPage from "./pages/ContentRatingPage";

function App() {
  return (
    <>
    <Routes>
      <Route path = "/" element = {<HomePage />}></Route>
      <Route path= "/login" element = {<LoginPage />}></Route>
      <Route path = "/sign-up" element = {<SignUpPage />}></Route>
      <Route path = "/:contentType/:id/" element = {<ContentPage />}></Route>
      <Route path = "/rating" element = {<ContentRatingPage />}></Route>
    </Routes>
    </>
  );
}

export default App;
