import React, { useState, useEffect } from 'react';
import axios from 'axios';
// import oneTeamPic from "./assets/1team.png";
// import twoTeamsPic from "./assets/2teams.png";
import video from "./assets/background2.mp4";

function TeamPreMatchAnalysis() {
    const [leagues, setLeagues] = useState([]);
    const [seasons, setSeasons] = useState([]);
    const [seasons2, setSeasons2] = useState([]);

    const [teams, setTeams] = useState([]);
    const [teams2, setTeams2] = useState([]);
    const [selectedLeague, setSelectedLeague] = useState('');
    const [selectedSeason, setSelectedSeason] = useState('');
    const [selectedSeason2, setSelectedSeason2] = useState('');
    const [selectedTeam, setSelectedTeam] = useState('');
    const [selectedTeam2, setSelectedTeam2] = useState('');
    const [event, setEvent] = useState('shooting');
    const [radarUrl, setRadarUrl] = useState('');
    const [reportUrl, setReportUrl] = useState('');

    const [twoTeams, setTwoTeams] = useState(true);

    const teamsMatrices = {
        "standard": ['Playing Time_MP', 'Playing Time_Starts', 'Playing Time_Min', 'Playing Time_90s', 'Performance_Gls', 'Performance_Ast', 'Performance_G+A', 'Performance_G-PK', 'Performance_PK', 'Performance_PKatt', 'Performance_CrdY', 'Performance_CrdR', 'Expected_xG', 'Expected_npxG', 'Expected_xAG', 'Expected_npxG+xAG', 'Progression_PrgC', 'Progression_PrgP'],
        "shooting": ['Standard_90s', 'Standard_Gls', 'Standard_Sh', 'Standard_SoT', 'Standard_SoT%', 'Standard_Sh/90', 'Standard_SoT/90', 'Standard_G/Sh', 'Standard_G/SoT', 'Standard_Dist', 'Standard_FK', 'Standard_PK', 'Expected_xG', 'Expected_npxG', 'Expected_npxG/Sh', 'Expected_G-xG', 'Expected_np:G-xG'],
        "passing": ['Total_Cmp', 'Total_Att', 'Total_Cmp%', 'Total_TotDist', 'Total_PrgDist', 'Short_Cmp', 'Short_Att', 'Short_Cmp%', 'Medium_Cmp', 'Medium_Att', 'Medium_Cmp%', 'Long_Cmp', 'Long_Att', 'Long_Cmp%', 'Ast', 'xAG', 'Expected_xA', 'Expected_A-xAG', 'KP', '1/3', 'PPA', 'CrsPA', 'PrgP'],
        "defense": ['Tackles_Tkl', 'Tackles_TklW', 'Tackles_Def 3rd', 'Tackles_Mid 3rd', 'Tackles_Att 3rd', 'Challenges_Tkl', 'Challenges_Att', 'Challenges_Tkl%', 'Challenges_Lost', 'Blocks', 'Blocks_Sh', 'Blocks_Pass', 'Int', 'Tkl+Int', 'Clr', 'Err'],
        "possession": ['Touches', 'Touches_Def Pen', 'Touches_Def 3rd', 'Touches_Mid 3rd', 'Touches_Att 3rd', 'Touches_Att Pen', 'Touches_Live', 'Take-Ons_Att', 'Take-Ons_Succ', 'Take-Ons_Succ%', 'Take-Ons_Tkld', 'Take-Ons_Tkld%', 'Carries', 'Carries_TotDist', 'Carries_PrgDist', 'Carries_PrgC', 'Carries_1/3', 'Carries_CPA', 'Carries_Mis', 'Carries_Dis', 'Receiving_Rec', 'Receiving_PrgR'],
        "misc": ['Performance_CrdY', 'Performance_CrdR', 'Performance_2CrdY', 'Performance_Fls', 'Performance_Fld', 'Performance_Off', 'Performance_Crs', 'Performance_Int', 'Performance_TklW', 'Performance_PKwon', 'Performance_PKcon', 'Performance_OG', 'Performance_Recov', 'Aerial Duels_Won', 'Aerial Duels_Lost', 'Aerial Duels_Won%']
    };

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/leagues').then((response) => {
            setLeagues(response.data);
        });
    }, []);

    useEffect(() => {
        if (selectedLeague) {
            axios.get('http://127.0.0.1:5000/seasons', { params: { league: selectedLeague, isPlayer: "false" } }).then((response) => {
                setSeasons(response.data);
            });
        }
    }, [selectedLeague]);

    useEffect(() => {
        if (selectedLeague) {
            axios.get('http://127.0.0.1:5000/seasons', { params: { league: selectedLeague, isPlayer: "false" } }).then((response) => {
                setSeasons2(response.data);
            });
        }
    }, [selectedLeague]);

    useEffect(() => {
        if (selectedLeague && selectedSeason) {
            axios.get('http://127.0.0.1:5000/teams', { params: { league: selectedLeague, season: selectedSeason, isPlayer: "false" } }).then((response) => {
                setTeams(response.data);
            });
        }
    }, [selectedLeague, selectedSeason]);

    useEffect(() => {
        if (selectedLeague && selectedSeason2) {
            axios.get('http://127.0.0.1:5000/teams', { params: { league: selectedLeague, season: selectedSeason2, isPlayer: "false" } }).then((response) => {
                setTeams2(response.data);
            });
        }
    }, [selectedLeague, selectedSeason2]);

    const fetchTeamRadar = () => {
        axios
            .get('http://127.0.0.1:5000/teamsRadar', {
                params: {
                    league: selectedLeague,
                    season: selectedSeason,
                    team: selectedTeam,
                    event: event,
                },
                responseType: 'blob',
            })
            .then((response) => {
                setRadarUrl(URL.createObjectURL(response.data));
            });
    };

    const fetchTeamReport = () => {
        axios
            .get('http://127.0.0.1:5000/teamReport', {
                params: {
                    league: selectedLeague,
                    season: selectedSeason,
                    team: selectedTeam,
                    event: event,
                },
                responseType: 'text',
            })
            .then((response) => {
                setReportUrl(response.data);
            });
    };

    const fetch2TeamRadar = () => {
        axios
            .get('http://127.0.0.1:5000/twoTeamsRadar', {
                params: {
                    league: selectedLeague,
                    season: selectedSeason,
                    season2: selectedSeason2,
                    team: selectedTeam,
                    team2: selectedTeam2,
                    event: event,
                },
                responseType: 'blob',
            })
            .then((response) => {
                setRadarUrl(URL.createObjectURL(response.data));
            });
    };

    return (
        <div className='grid grid-cols-7 p-5 text-white'>
            <div className='fixed top-0 left-0 w-full h-full object-cover z-[-1] bg-black bg-opacity-80'></div>
            <video autoPlay muted loop className='fixed top-0 left-0 w-full h-full object-cover z-[-2]' > <source src={video} type='video/mp4' /> </video>
            <div className='col-span-7 text-center p-10 text-3xl font-semibold flex flex-row gap-10 justify-center items-center'>
                Try analysis on 
                <button onClick={() => setTwoTeams(false)} className='rounded-md bg-green-600 px-5 py-3 text-white'>
                    1 Team
                </button>
                <button onClick={() => setTwoTeams(true)} className='rounded-md bg-green-600 px-5 py-3 text-white'>
                    2 Teams
                </button>
            </div>
            <div className={twoTeams ? "container mx-auto p-4 col-span-3" : "container mx-auto p-4 col-span-7"}>
                <h1 className="text-2xl font-bold mb-4">Soccer Team Radar Charts</h1>
                <div className="mb-4">
                    <label className="block mb-2">League</label>
                    <select
                        className="border p-2 w-full text-black"
                        value={selectedLeague}
                        onChange={(e) => setSelectedLeague(e.target.value)}
                    >
                        <option value="">Select League</option>
                        {leagues.map((league) => (
                            <option key={league} value={league}>
                                {league}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="mb-4">
                    <label className="block mb-2">Season</label>
                    <select
                        className="border p-2 w-full text-black"
                        value={selectedSeason}
                        onChange={(e) => setSelectedSeason(e.target.value)}
                    >
                        <option value="">Select Season</option>
                        {seasons.map((season) => (
                            <option key={season} value={season}>
                                {season}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="mb-4">
                    <label className="block mb-2">Team</label>
                    <select
                        className="border p-2 w-full text-black"
                        value={selectedTeam}
                        onChange={(e) => setSelectedTeam(e.target.value)}
                    >
                        <option value="">Select Team</option>
                        {teams.map((team) => (
                            <option key={team} value={team}>
                                {team}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="mb-4">
                    <label className="block mb-2">Event</label>
                    <select
                        className="border p-2 w-full text-black"
                        value={event}
                        onChange={(e) => setEvent(e.target.value)}
                    >
                        {Object.keys(teamsMatrices).map((eventKey) => (
                            <option key={eventKey} value={eventKey}>
                                {eventKey}
                            </option>
                        ))}
                    </select>
                </div>
                {twoTeams ? <></> :
                <div className='flex flex-row gap-5'>
                    <button className="bg-blue-500 text-white p-2" onClick={fetchTeamReport}>
                            Generate Report
                        </button>
                    <button className="bg-blue-500 text-white p-2" onClick={fetchTeamRadar}>
                        Generate Radar Chart
                    </button>
                </div>}
               
            </div>
            {twoTeams ? <div className='text-5xl font-bold col-span-1 self-center text-center'> VS </div> : <></>}
            {twoTeams ? 
                <div className="container mx-auto p-4 col-span-3">
                    <h1 className="text-2xl font-bold mb-4">Soccer Team Radar Charts</h1>
                    <div className="mb-4">
                        <label className="block mb-2">League</label>
                        <select
                            className="border p-2 w-full text-black"
                            value={selectedLeague}
                            onChange={(e) => setSelectedLeague(e.target.value)}
                        >
                            <option value="">Select League</option>
                            {leagues.map((league) => (
                                <option key={league} value={league}>
                                    {league}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="mb-4">
                        <label className="block mb-2">Season</label>
                        <select
                            className="border p-2 w-full text-black"
                            value={selectedSeason2}
                            onChange={(e) => setSelectedSeason2(e.target.value)}
                        >
                            <option value="">Select Season</option>
                            {seasons2.map((season) => (
                                <option key={season} value={season}>
                                    {season}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="mb-4">
                        <label className="block mb-2">Team</label>
                        <select
                            className="border p-2 w-full text-black"
                            value={selectedTeam2}
                            onChange={(e) => setSelectedTeam2(e.target.value)}
                        >
                            <option value="">Select Team</option>
                            {teams2.map((team) => (
                                <option key={team} value={team}>
                                    {team}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="mb-4">
                        <label className="block mb-2">Event</label>
                        <select
                            className="border p-2 w-full text-black"
                            value={event}
                            onChange={(e) => setEvent(e.target.value)}
                        >
                            {Object.keys(teamsMatrices).map((eventKey) => (
                                <option key={eventKey} value={eventKey}>
                                    {eventKey}
                                </option>
                            ))}
                        </select>
                    </div>
                </div> : <></>    
            }
            {twoTeams ? 
                <div className='items-center justify-center flex col-span-7'>
                    <button className="bg-blue-500 text-white p-2" onClick={fetch2TeamRadar}>
                        Generate Radar Chart
                    </button>
                </div> : <></>    
            }
            {reportUrl && (
                <div className="mt-4 col-span-7 items-center flex flex-col">
                    <h2 className="text-xl font-bold">Report</h2>
                    <div className='w-[50vw] whitespace-pre-wrap'>
                        {reportUrl}
                    </div>
                </div>
            )}
            {radarUrl && (
                <div className="mt-4 col-span-7 items-center flex flex-col">
                    <h2 className="text-xl font-bold">Radar Chart</h2>
                    <img src={radarUrl} alt="Radar Chart" className='w-[50vw] ' />
                </div>
            )}
        </div>
    );
}

export default TeamPreMatchAnalysis;
