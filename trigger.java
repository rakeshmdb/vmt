import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import com.mongodb.client.model.changestream.FullDocument;
import org.bson.Document;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.data.mongodb.MongoDatabaseFactory;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.List;

@Service
public class ChangeStreamService {

    @Autowired
    private MongoTemplate mongoTemplate;

    @Autowired
    private MongoClient mongoClient;

    @PostConstruct
    public void init() {
        MongoDatabase database = mongoClient.getDatabase("your_database_name");
        MongoCollection<Document> collection = database.getCollection("CLMT_PYMT_GST_AR");

        collection.watch(List.of()).fullDocument(FullDocument.UPDATE_LOOKUP).forEach((ChangeStreamDocument<Document> changeStreamDocument) -> {
            if (changeStreamDocument.getOperationType().getValue().equals("insert")) {
                Document document = changeStreamDocument.getFullDocument();
                if (document.get("REF_NO") == null) {
                    Long newRefNo = getNextSequenceValue();
                    document.put("REF_NO", newRefNo);
                    collection.replaceOne(new Document("_id", document.get("_id")), document);
                }
            }
        });
    }

    private Long getNextSequenceValue() {
        MongoCollection<Document> seqCollection = mongoClient.getDatabase("your_database_name").getCollection("sequences");
        Document seqDoc = seqCollection.findOneAndUpdate(
                new Document("_id", "CLMT_PYMT_GST_REF_NO_SEQ"),
                new Document("$inc", new Document("seq", 1))
        );
        if (seqDoc == null) {
            seqCollection.insertOne(new Document("_id", "CLMT_PYMT_GST_REF_NO_SEQ").append("seq", 1));
            return 1L;
        }
        return seqDoc.getLong("seq");
    }
}
