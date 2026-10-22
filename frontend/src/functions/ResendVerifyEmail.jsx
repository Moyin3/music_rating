import post from "./post";

const ResendVerifyEmail = async(email) =>{
    /* Once again proper error handling required here, also should not run request
    if original sign up is not valid */
const response = await post({"url": "/api/dj-rest-auth/registration/resend-email/", "data": {"email": email.toLowerCase()}});
return(
    response
)
}
export default ResendVerifyEmail;