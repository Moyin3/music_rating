import {useState} from "react";
import post from "../functions/post";

const ResetPasswordForm = ({uid, token}) =>{
    const [password1, setPassword1] = useState("");
    const [password2, setPassword2] = useState("");
    const data = {uid, token, "new_password1": password1, "new_password2": password2};
    
    const handleSubmit = async(event) => {
        event.preventDefault();
        const response = await post({"url": "/api/dj-rest-auth/password/reset/confirm/", "data": data});
        console.log(response);
    }
return(
    <form onSubmit={handleSubmit}>
        <label>New Password</label>
        <input type = "password" value = {password1} onChange = {(e) => setPassword1(e.target.value)} />
        <label>Confirm New Password</label>
        <input type = "password" value = {password2} onChange = {(e) => setPassword2(e.target.value)} />
        <button type = "submit">Submit</button>
    </form>
)
}
export default ResetPasswordForm;