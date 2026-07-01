import React from 'react';
import { Link } from "react-router";



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