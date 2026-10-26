import { useState, useEffect } from 'react';
import ResendVerifyEmail from "../functions/ResendVerifyEmail";
import styles from "./styles/SignUpForm.module.css";
import GoogleLoginButton from "../functions/GoogleAuth";
const SignUpForm = () => {
    const [isVisible, setVisible] = useState(false);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');
    

    // replaces alert, alertVisible, success, successVisible, closeAlert, closeSuccess
    const [notice, setNotice] = useState(null);

    const handleResend = async () =>{
        const result = await ResendVerifyEmail(email);
        if (result.status === "success"){
            setNotice({type: "success", messages: ["Verification email has been resent."]})
        } else{
            /* Just realised the backend actually gives a response
            should use that instead of this message */
            const body = result.json;
            const messages = Object.entries(body).flatMap(
                ([field, msgs]) => [].concat(msgs).map(m => `${field}: ${m}`)
            );
            setNotice({type: "alert", messages });
        }
    }

    const handleSubmit = async (event) => {
        event.preventDefault();
        setNotice(null);

        const data = { username, password1, password2, email: email.toLowerCase() };

        try {
            const response = await fetch("/api/dj-rest-auth/registration/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });
            const body = await response.json();

            if (response.ok) {
                setNotice({ type: "success", messages: ["Sign up successful. Please verify your email."] });
            } else {
                const messages = Object.entries(body).flatMap(
                    ([field, msgs]) => [].concat(msgs).map(m => `${field}: ${m}`)
                );
                setNotice({ type: "alert", messages });
            }
        } catch (error) {
            console.error("Error:", error);
            setNotice({ type: "alert", messages: ["Something went wrong. Please try again."] });
        }
    };
     return (
        <>
        <form className = {styles.signUpForm}>
            <div className={styles.signUpUsername}>
            <label>Username</label>
            <input type = "text" value = {username} placeholder='Username' autoComplete = 'username' onChange={(e) => setUsername(e.target.value)}/>
            </div>

            <div className={styles.signUpEmail}>
            <label>Email</label>
            <input type= "email" value = {email} placeholder='FrankOceancomeback@gmail.com' autoComplete='email' onChange={(e) => setEmail(e.target.value)}/>
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
            <button type = "button" className = {styles.resendEmail} onClick = {handleResend}>Resend Email Verification</button>
        )}
        </form>
        {notice && (
    <div className={notice.type}>
        <span className={styles.closeBtn} onClick={() => setNotice(null)}>&times;</span>
        <ul>{notice.messages.map(m => <li key={m}>{m}</li>)}</ul>
    </div>
    )}
     </>
    );
};
export default SignUpForm;