import { useState } from 'react';
import ResendVerifyEmail from "../functions/ResendVerifyEmail";
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
        <form>
            <label>Username:</label>
            <input type = "text" value = {username} onChange={(e) => setUsername(e.target.value)}/>

            <label>Email:</label>
            <input type= "email" value = {email} onChange={(e) => setEmail(e.target.value)}/>

            <label>Set Password:</label>
            <input type = "password" value = {password1} onChange={(e) => setPassword1(e.target.value)}/>

            <label>Make Sure Password Matches:</label>
            <input type = "password" value = {password2} onChange= {(e) => setPassword2(e.target.value)}/>
            
            <button onClick ={(event) =>{
                handleSubmit(event);
                setVisible(true);
            }}>Sign Up</button>
        </form>
        {isVisible &&(
            <button onClick = {() => ResendVerifyEmail(email)}>Resend Email Verification</button>
        )}
        </>
    );
};

export default SignUpForm;