import { useState } from 'react';

const SignUpPage = () => {
    const [isVisible, setVisible] = useState(false);
    const [isSubmitted, setSubmitted] = useState(false);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');

    function openSignUpForm() {
        setVisible(true);
    }
    const handleSubmit = async (event) => {
        event.preventDefault();

    const data = { username, password1, password2, email };

    
    try {
        const response = await fetch ("http://127.0.0.1:8000/api/dj-rest-auth/registration/", {
            method: "POST", 
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)

        });
        
        if (!response.ok) {
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
        SignUpButton
        </>
    );
};

export default SignUpForm;