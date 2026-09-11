import post from "../functions/post";

const VerifyEmail = async(data) =>{
const response = await post({"url": "/api/auth/registration/verify-email/", "data": data});
console.log(data)
console.log("What is happening to verification", response);
return response;
}
export default VerifyEmail;