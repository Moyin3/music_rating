import React from 'react';
import { BrowserRouter, Link } from "react-router";



const LoginButton = () => {
    return(
        <>
        <Link to= "/login">
    <button>Login</button>
    </Link>
    </>
    )
}
export default LoginButton;