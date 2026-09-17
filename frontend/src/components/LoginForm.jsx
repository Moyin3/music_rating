import { useState, useContext } from 'react';
import LoginCheck from '../functions/LoginCheck';
import post from '../functions/post';
import { useLocation, useNavigate, Link } from "react-router";
import AuthContext from '../functions/AuthContext';
import GoogleLoginButton from "../functions/GoogleAuth";

const LoginForm = () => {
    const [value, setValue] = useState('');
    const [password, setPassword] = useState('');
    const { user, setUser } = useContext(AuthContext);
    const location = useLocation();
    const navigate = useNavigate();
    // This is data that has been given for the original route, but ended up in the redirect 
    const priorData = location.state?.priorData?.Data; 
    const handleSubmit = async (event) => {
        event.preventDefault();
    
    const data = value.includes('@') ? {email: value.toLowerCase(), password} : {username: value, password};

    const response = await post({"url": "http://127.0.0.1:8000/api/dj-rest-auth/login/", "data": data})
    
    if (response.status == "success"){
        console.log(response)
        setUser(await LoginCheck());
        navigate(location.state?.priorData?.location?.pathname || "/", {replace: true, state: {priorData}});
    }else if (response.status == "error: request failed"){
        //TODO: Do this later
    }else{
        //Serious Headache
    }
    console.log(await LoginCheck());


    };
    return (
        <>
        <GoogleLoginButton />
        <form onSubmit = {handleSubmit}>
        <label>Username/Email:</label>
        <input type = "text" value = {value} onChange={(e) => setValue(e.target.value)}/>

        <label>Password:</label>
        <input type = "password" value = {password} onChange={(e) => setPassword(e.target.value)}/>
        
        <button type = "submit">Login</button>
        </form>
        <Link to = "/forgot-password/">
        <button type = "button">Forget Password</button>
        </Link>
        </>
    );
    };

export default LoginForm;
    