import post from "./post";

const ResendVerifyEmail = async(email) =>{
    /* Once again proper error handling required here, also should not run request
    if original sign up is not valid */
const [message, setMessage] = useState(null);
const response = await post({"url": "/api/dj-rest-auth/registration/resend-email/", "data": {"email": email.toLowerCase()}});
if (response.ok){
    setMessage({type: "success", text: Array.isArray(first) ? first[0] : first});
}else{
    setMessage({type: "alert", text: Array.isArray(first) ? first[0] : first});
}
return(
    {message && (
        <div className = {message.type}>
            <span className = "closeBtn" onClick = {() => setMessage(null)}>&times;</span>
            {message.text}
        </div>
    )};
)
}
export default ResendVerifyEmail;