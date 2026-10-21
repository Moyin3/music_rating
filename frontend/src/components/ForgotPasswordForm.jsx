import {useState} from "react";
import post from "../functions/post";
import styles from "./styles/ForgotPasswordForm.module.css";

const ForgotPasswordForm = () => {
    const [email, setEmail] = useState("");
    const [message, setMessage] = useState(null);

    const handleSubmit = async(event) =>{
        event.preventDefault();
        const response = await post({"url": "/api/dj-rest-auth/password/reset/", "data": {"email": email.toLowerCase()}});
        console.log(response);
        if (response.status === "success"){
            setMessage({type: "success", text: "An email has been sent"});
        }else{
            setMessage({type: "alert", text: "Something has gone wrong, please try again"})
        }
    }
    return(
        <>
        <main className = {styles.forgotPasswordMain}>
    <form className = {styles.forgotPasswordForm} onSubmit={handleSubmit}>
        <div className = {styles.heading}>
        <h3>Reset Password</h3>
        <p className = {styles.desc}>Enter the email associated with your account.</p>
        </div>
        <div className = {styles.forgotPasswordInput}>
        <label>Email</label>
        <input  className = {styles.emailInput} type = "email" autoComplete="email" value = {email} onChange = {(e) => setEmail(e.target.value)}/>
        </div>
        <button className = {styles.submit} type = "submit">Submit</button>
    </form>
    {message && (
    <div className = {message.type}>
        <span className = "closeBtn" onClick = {() => setMessage(null)}>&times;</span>
        {message.text}
    </div>
    )}
    </main>
    </>
    )
}

export default ForgotPasswordForm;