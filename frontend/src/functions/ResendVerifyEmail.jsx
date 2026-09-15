import post from "./post";

const ResendVerifyEmail = async(email) =>{
const response = await post({"url": "/api/auth/registration/resend-email/", "data": {"email": email.toLowerCase()}});
console.log({"url": "/api/auth/registration/resend-email/", "data": {"email": email}});
console.log(email)
return response;
}
export default ResendVerifyEmail;