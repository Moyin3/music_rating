import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import { Routes, Route } from "react-router";
import SignUpPage from "./pages/SignUpPage";
import ContentPage from "./pages/ContentPage";
import ContentRatingPage from "./pages/ContentRatingPage";
import ProtectedRoute from "./components/ProtectedRoute";
import { useState, useEffect, createContext, useContext } from "react";
import LoginCheck from "./functions/LoginCheck";
import AuthContext from "./functions/AuthContext";
import ReviewsPage from "./pages/ReviewsPage";

function App() {
  const [checked, setChecked] = useState(false);
  const {user, setUser} = useContext(AuthContext);
  
  
  useEffect(() => {
    const doLoginCheck = async () =>{
      setUser(await LoginCheck());
      setChecked(true);
    }
    doLoginCheck();
  },[])
  console.log("What does user look like?", user)
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
      <Route path = "/reviews/:username" element = {<ReviewsPage />}></Route>
    </Routes>
    </>
  );
}

export default App;
