import Searchbar from "./Searchbar";
import LoginButton from "./LoginButton";

export default function Navigationbar(){
    return(
        <div>
            <a className="Home">Home</a>
            <Searchbar />
            <a className="Artists">Artists</a>
            <a className="Albums">Albums</a>
            <a className="Tracks">Tracks</a>
            <LoginButton />
        </div>
    )
}
