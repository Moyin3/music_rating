import { useEffect, useRef } from "react";
import { handleGoogleCallback } from "../functions/GoogleAuth";
import NavigationBar from "../components/Navigationbar";
import { useNavigate } from "react-router";


const GoogleCallbackPage = () =>{
const navigate = useNavigate();
const calledRef = useRef(false);
useEffect(()=>{
    if (calledRef.current) return;
    calledRef.current = true;
    handleGoogleCallback().then((result) => {
        if (result.success) {
            navigate('/')
        } else{
            navigate('/login?error=1');
        }
    })
}, []);
return(
    <>
    <NavigationBar />
    <div>Logging in...</div>
    </>
)
}

export default GoogleCallbackPage;