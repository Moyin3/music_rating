import { useState } from 'react';

const Loginform = () => {
    const [isVisible, setVisible] = useState(false);
    const [isSubmitted, setSubmitted] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    

    function openLoginForm() {
        setVisible(true);
    }

    const handleSubmit = async (event) => {
        event.preventDefault();

    const data = { username, email, password };

    try {
        const response = await fetch("http://127.0.0.1:8000/api/dj-rest-auth/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok){
            throw new Error('Something went wrong');
        }
        const result = await response.json();
        console.log(result);
    } catch (error) {
        console.error("Error:", error)
    }
    };
    return (
        <>
        <button onClick = {openLoginForm}>Login</button>
        {isVisible &&(
        <form>
            <label>Username:</label>
            <input type = "text" value = {username} onChange={(e) => setUsername(e.target.value)}/>

            <label>Email:</label>
            <input type= "email" value = {email} onChange={(e) => setEmail(e.target.value)}/>

            <label>Password:</label>
            <input type = "password" value = {password} onChange={(e) => setPassword(e.target.value)}/>
            
            <button onClick = {handleSubmit}>Login</button>
        </form>

        )
}
        </>
    );
    };

export default Loginform;