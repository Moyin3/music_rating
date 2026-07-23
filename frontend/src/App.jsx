import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import { Routes, Route } from "react-router";
import SignUpPage from "./pages/SignUpPage";
import ContentPage from "./pages/ContentPage";
import ContentRatingPage from "./pages/ContentRatingPage";
import ProtectedRoute from "./components/ProtectedRoute";
import { useState, useEffect, createContext } from "react";
import LoginCheck from "./functions/LoginCheck";

function App({user}) {
  const [checked, setChecked] = useState(false);
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    const doLoginCheck = async () =>{
      setUser(await LoginCheck());
      setChecked(true);
    }
    doLoginCheck();
  },[])
  return (
    <>
    <Routes>
      <Route path = "/" element = {<HomePage />}></Route>
      <Route path= "/login" element = {<LoginPage />}></Route>
      <Route path = "/sign-up" element = {<SignUpPage />}></Route>
      <Route path = "/:contentType/:id/" element = {<ContentPage />}></Route>
      <Route element = {<ProtectedRoute isAuthenticated = {!!user}/>}>
      <Route path = "/rating" element = {<ContentRatingPage />}></Route>
      </Route>
    </Routes>
    </>
  );
}

export default App;
