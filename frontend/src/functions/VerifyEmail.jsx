import post from "../functions/post";

const VerifyEmail = async(data) =>{
const response = await post({"url": "/api/dj-rest-auth/registration/verify-email/", "data": data});
return response;
}
export default VerifyEmail;