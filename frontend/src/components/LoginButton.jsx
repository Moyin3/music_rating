import {useState} from 'react'

const [isVisible, setVisible] = useState(false);

function openLoginForm() {
        setVisible(true);
    }

function LoginButton({OpenLoginForm}) {
    return(
    <button onClick={OpenLoginForm}>Login</button>
    )
}
export default LoginButton;