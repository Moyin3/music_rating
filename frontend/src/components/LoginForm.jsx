import { useState, useContext } from 'react';
import LoginCheck from '../functions/LoginCheck';
import post from '../functions/post';
import { useLocation, useNavigate, Link } from "react-router";
import AuthContext from '../functions/AuthContext';
import GoogleLoginButton from "../functions/GoogleAuth";
import styles from "./styles/LoginForm.module.css";

const LoginForm = () => {
    const [value, setValue] = useState('');
    const [password, setPassword] = useState('');
    const [alert, setAlert] = useState('');
    const [alertVisible, setAlertVisible] = useState(false);
    const { user, setUser } = useContext(AuthContext);
    const location = useLocation();
    const navigate = useNavigate();
    // This is data that has been given for the original route, but ended up in the redirect 
    const priorData = location.state?.priorData?.Data; 

    const closeAlert = () =>{
        setAlertVisible(false);
    }

    const handleSubmit = async (event) => {
        event.preventDefault();
    
    const data = value.includes('@') ? {email: value.toLowerCase(), password} : {username: value, password};

    const response = await post({"url": "http://127.0.0.1:8000/api/dj-rest-auth/login/", "data": data})
    
    const first = Object.values(response.json)[0];

    if (response.status == "success"){
        console.log(response)
        setUser(await LoginCheck());
        navigate(location.state?.priorData?.location?.pathname || "/", {replace: true, state: {priorData}});
    }else if (response.status == "error: request failed"){
        setAlert(Array.isArray(first) ? first[0] : first);
        setAlertVisible(true);
    }else{
        setAlert(Array.isArray(first) ? first[0] : first);
        setAlertVisible(true);
    }
    console.log(await LoginCheck());


    };
    return (
        <>
        <form className={styles.loginForm} onSubmit = {handleSubmit}>
        <div className = {styles.loginUsername}>
        <label >Username/Email</label>
        <input type = "text" value = {value} onChange={(e) => setValue(e.target.value)}/>
        </div>

        <div className = {styles.loginPassword}>
        <label>Password</label>
        <input type = "password" value = {password} autoComplete='current-password' onChange={(e) => setPassword(e.target.value)}/>
        <Link to = "/forgot-password/" className={styles.forgotPassword}>
        Forgot password
        </Link>
        </div>
                <button className={styles.loginButton} type = "submit">Login</button>
        <GoogleLoginButton className={styles.gmailButton} name = "Continue with Google" />
        </form>
        {alertVisible && <div className = "alert">
            <span className = "closeBtn" onClick = {closeAlert}>
                &times;
            </span>
            {alert}
        </div>}
        </>
    );
    };

export default LoginForm;
    