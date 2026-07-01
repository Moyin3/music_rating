import Searchbar from "./SearchBar";
import LoginButton from "./LoginButton";
import { BrowserRouter, Link } from "react-router";

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
            <LoginButton />
        </div>
    )
}

export default NavigationBar;
