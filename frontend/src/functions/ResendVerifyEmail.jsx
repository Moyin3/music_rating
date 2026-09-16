import post from "./post";

const ResendVerifyEmail = async(email) =>{
const response = await post({"url": "/api/dj-rest-auth/registration/resend-email/", "data": {"email": email.toLowerCase()}});
return response;
}
export default ResendVerifyEmail;