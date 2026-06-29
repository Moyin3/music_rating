 
 const SignUpButton = () => {
 
 <button onClick = {openSignUpForm}>Sign up</button>
        {
        <form>
            <label>Username:</label>
            <input type = "text" value = {username} onChange={(e) => setUsername(e.target.value)}/>

            <label>Email:</label>
            <input type= "email" value = {email} onChange={(e) => setEmail(e.target.value)}/>

            <label>Set Password:</label>
            <input type = "password" value = {password1} onChange={(e) => setPassword1(e.target.value)}/>

            <label>Make Sure Password Matches:</label>
            <input type = "password" value = {password2} onChange= {(e) => setPassword2(e.target.value)}/>
            
            <button onClick = {handleSubmit}>Sign Up</button>
        </form>
        };
 };

export default SignUpButton;