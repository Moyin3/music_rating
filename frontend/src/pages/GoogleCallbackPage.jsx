import { useEffect, useRef, useContext } from "react";
import { handleGoogleCallback } from "../functions/GoogleAuth";
import NavigationBar from "../components/Navigationbar";
import { useNavigate } from "react-router";
import LoginCheck from "../functions/LoginCheck";
import AuthContext from '../functions/AuthContext';

const GoogleCallbackPage = () =>{
const navigate = useNavigate();
const calledRef = useRef(false);
const { user, setUser } = useContext(AuthContext);

useEffect(()=>{
    if (calledRef.current) return;
    calledRef.current = true;
    handleGoogleCallback().then(async (result) => {
        if (result.success) {
            setUser(await LoginCheck());
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