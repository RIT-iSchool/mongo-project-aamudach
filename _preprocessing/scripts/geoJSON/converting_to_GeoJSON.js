const connection = new Mongo(`localhost:27017`),
      db = connection.getDB( `project` ),
      geoColl = db.getCollection( `businesses` ); 

geoColl.updateMany(
{},
[
    {
    $set: 
        {
            location: {
            $cond: 
                {
                    if: { $or: [
                    {$eq: ["$longitude", ""]},
                    {$eq: ["$latitude", ""]}
                    ]},
                    then: null,
                    else: {
                    type: `Point`,
                    coordinates: ["$longitude", "$latitude"]
                    }
                }
            }
        }
    },
    {
    $unset: [`longitude`, `latitude`] //remove original long lat from JSON Objects (documents)
    }
]
);