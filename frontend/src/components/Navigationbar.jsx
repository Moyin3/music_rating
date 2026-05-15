import Searchbar from "./Searchbar";
import LoginForm from "./loginpage";
import SignUpForm from "./signuppage";

export default function Navigationbar(){
    return(
        <div>
            <a className="Home">Home</a>
            <Searchbar />
            <a className="Artists">Artists</a>
            <a className="Albums">Albums</a>
            <a className="Tracks">Tracks</a>
            <LoginForm />
            <SignUpForm />
        </div>
    )
}
