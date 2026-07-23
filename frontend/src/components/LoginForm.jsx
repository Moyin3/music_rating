import { useState } from 'react';
import LoginCheck from '../functions/LoginCheck';
import post from '../functions/post';
import { useLocation } from "react-router";

const LoginForm = ({user}) => {
    const [isSubmitted, setSubmitted] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    

    const handleSubmit = async (event) => {
        event.preventDefault();

    const data = { username, email, password };

    const response = await post({"url": "http://127.0.0.1:8000/api/dj-rest-auth/login/", "data": data})

    if (response.status == "success"){
        console.log(response)

    }else if (response.status == "error: request failed"){
        //TODO: Do this later
    }else{
        //Serious Headache
    }
    console.log(await LoginCheck());

    };
    return (
        <>
        <form>
        <label>Username:</label>
        <input type = "text" value = {username} onChange={(e) => setUsername(e.target.value)}/>

        <label>Email:</label>
        <input type= "email" value = {email} onChange={(e) => setEmail(e.target.value)}/>

        <label>Password:</label>
        <input type = "password" value = {password} onChange={(e) => setPassword(e.target.value)}/>
        
        <button onClick = {handleSubmit}>Login</button>
        </form>
        </>
    );
    };

export default LoginForm;
    