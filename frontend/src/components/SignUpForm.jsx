import { useState } from 'react';
import ResendVerifyEmail from "../functions/ResendVerifyEmail";
import styles from "./styles/SignUpForm.module.css";
import GoogleLoginButton from "../functions/GoogleAuth";
const SignUpForm = () => {
    const [isVisible, setVisible] = useState(false);
    const [isSubmitted, setSubmitted] = useState(false);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();

    const data = { username, password1, password2, "email": email.toLowerCase()};

    
    try {
        const response = await fetch ("http://127.0.0.1:8000/api/dj-rest-auth/registration/", {
            method: "POST", 
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)

        });
        
        if (!response.ok) {
            throw new Error('Something went wrong');
        }

        const result = await response.json();
        console.log(result);
    } catch (error) {
        console.error("Error:", error)
    }
};
     return (
        <>
        <form className = {styles.signUpForm}>
            <div className={styles.signUpUsername}>
            <label>Username</label>
            <input type = "text" value = {username} placeholder='Username' onChange={(e) => setUsername(e.target.value)}/>
            </div>

            <div className={styles.signUpEmail}>
            <label>Email</label>
            <input type= "email" value = {email} placeholder='FrankOceancomeback@gmail.com' onChange={(e) => setEmail(e.target.value)}/>
            </div>

            <div className = {styles.signUpPassword}>
            <label>Password</label>
            <input type = "password" value = {password1} placeholder='Password' autoComplete="new-password" onChange={(e) => setPassword1(e.target.value)}/>
            </div>

            <div className = {styles.signUpConfirmPassword}>
            <label>Confirm Password</label>
            <input type = "password" value = {password2} placeholder='Password' autoComplete='new-password' onChange= {(e) => setPassword2(e.target.value)}/>
            </div>
            
            <button className = {styles.signUpButton} onClick ={(event) =>{
                handleSubmit(event);
                setVisible(true);
            }}>Sign Up</button>
        
           <GoogleLoginButton name = "Continue with Google"  className = {styles.gmailButton}/>
        {isVisible &&(
            <button className = {styles.resendEmail} onClick = {() => ResendVerifyEmail(email)}>Resend Email Verification</button>
        )}
        </form>
        </>
    );
};

export default SignUpForm;