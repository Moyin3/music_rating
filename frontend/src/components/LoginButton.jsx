import React from 'react';
import { Link } from "react-router";
import { useContext } from "react"
import AuthContext from '../functions/AuthContext';
import styles from './styles/LoginButton.module.css';



const LoginButton = () => {
    const {user, setUser} = useContext(AuthContext);
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
        </div>
        </div>
        </>
    )}
    </>
    )
}
export default LoginButton;