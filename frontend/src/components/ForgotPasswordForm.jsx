import {useState} from "react";
import post from "../functions/post";

const ForgotPasswordForm = () => {
    const [email, setEmail] = useState("");
    const handleSubmit = async(event) =>{
        event.preventDefault();
        const response = await post({"url": "/api/dj-rest-auth/password/reset/", "data": {"email": email.toLowerCase()}});
        console.log(response);
    }
    return(
        <>
        <h3>Reset Password</h3>
        <p>Enter the email associated with your account.</p>
    <form onSubmit={handleSubmit}>
        <label>Email</label>
        <input type = "email" value = {email} onChange = {(e) => setEmail(e.target.value)}/>
        <button type = "submit">Submit</button>
    </form>
    </>
    )
}

export default ForgotPasswordForm;