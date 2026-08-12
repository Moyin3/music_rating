import React from 'react';
import { Link } from "react-router";
import { useContext } from "react"
import AuthContext from '../functions/AuthContext';
import styles from './styles/LoginButton.module.css';
import post from '../functions/post';



const LoginButton = () => {
    const {user, setUser} = useContext(AuthContext);
    const LogOut = async(event) =>{
        event.preventDefault();


        const response = await post({"url": "http://127.0.0.1:8000/api/dj-rest-auth/logout/", "data": []})

        if (response.status == "success"){
            console.log(response)
            setUser(null);
        }else if (response.status == "error: request failed"){

        }else{

        }
    }
    return(
        <>{user == null &&(
        <>
        <Link to= "/login">
    <button>Login</button>
    </Link>
    </>
    )}
    {user &&(
        <>
        <div className = {styles.dropdown}>
        <button className = {styles.dropbtn}>{user.username}</button>
        <div className = {styles["dropdown-content"]}>
            <Link to= {`/reviews/${user.username}`} state = {user.username}>
            {console.log("username data sent to reviews page", user.username)}
            <p>Ratings</p>
            </Link>
            <button onClick={LogOut}>Log Out</button>
        </div>
        </div>
        </>
    )}
    </>
    )
}
export default LoginButton;