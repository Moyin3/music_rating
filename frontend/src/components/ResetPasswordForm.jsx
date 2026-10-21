import {useState} from "react";
import post from "../functions/post";
import styles from "./styles/ResetPasswordForm.module.css";

const ResetPasswordForm = ({uid, token}) =>{
    const [password1, setPassword1] = useState("");
    const [password2, setPassword2] = useState("");
    const [message, setMessage] = useState(null);
    const data = {uid, token, "new_password1": password1, "new_password2": password2};
    
    const handleSubmit = async(event) => {
        event.preventDefault();
        const response = await post({"url": "/api/dj-rest-auth/password/reset/confirm/", "data": data});
        console.log(response);

        /* To be very honest, I'm not a fan of this, feels like I'm just taking
        the first value from a list, which might not be what I want, need to go
        over this. */
        const first = Object.values(response.json)[0];

        if (response.status === "success"){
            setMessage({ type: "success", text: Array.isArray(first) ? first[0] : first});
        }else{
            setMessage({ type: "alert", text:Array.isArray(first) ? first[0] : first});
        }
    }
return(
    <main className = {styles.resetMain}>
    <form className = {styles.resetForm} onSubmit={handleSubmit}>
        <h2 className = {styles.resetTitle}>Reset Password</h2>
        <div className = {styles.passwordReset}>
        <label>New Password</label>
        <input type = "password" value = {password1} onChange = {(e) => setPassword1(e.target.value)} />
        </div>
        <div className = {styles.confirmPasswordReset}>
        <label>Confirm New Password</label>
        <input type = "password" autoComplete="new-password" value = {password2} onChange = {(e) => setPassword2(e.target.value)} />
        </div>
        <button className = {styles.submit} type = "submit">Submit</button>
    </form>
    {message && (
    <div className = {message.type}>
        <span className = "closeBtn" onClick = {() => setMessage(null)}>
            &times;
        </span>
        {message.text}
        </div>
    )}
    </main>
)
}
export default ResetPasswordForm;