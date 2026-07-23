import { useState } from 'react';
import LoginForm from '../components/LoginForm';
import NavigationBar from '../components/Navigationbar';

const LoginPage = ({user}) => {
    console.log("sending the user", {user})
    return(
    <>
    <NavigationBar />
    <LoginForm user = {user}/>
    </>
    )
}

       

export default LoginPage;