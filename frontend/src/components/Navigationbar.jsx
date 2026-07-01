import Searchbar from "./SearchBar";
import LoginButton from "./LoginButton";
import { BrowserRouter, Link } from "react-router";
import SignUpButton from "./SignUpButton";

const NavigationBar = () => {
    return(
        <div>
            <Link to= "/">
            <button>Home</button>
            </Link>
            <Searchbar />
            <button>Artists</button>
            <button>Albums</button>
            <button>Tracks</button>
            <SignUpButton />
            <LoginButton />
        </div>
    )
}

export default NavigationBar;
